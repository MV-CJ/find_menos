from flask_restful import Api, Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
from resources.normalize import normalize_path_params
from models.site import SiteModel
import sqlite3


normalize_path_params()

# Filtros
path_params = reqparse.RequestParser()
path_params.add_argument("cidade",type=str, default="", location="args")
path_params.add_argument("estrelas_min",type=float, default=0, location="args")
path_params.add_argument("estrelas_max",type=float, default=99999, location="args")
path_params.add_argument("diaria_min",type=float, default=0, location="args")
path_params.add_argument("diaria_max",type=float, default=99999999999, location="args")
path_params.add_argument("page",type=float, default=1, location="args")
path_params.add_argument("per_page",type=float, default=100, location="args")

#Retorna todos os meus hoteis criados.
class Hoteis(Resource):
    query_params = reqparse.RequestParser()
    query_params.add_argument("cidade", type=str, default="", location="args")
    query_params.add_argument("estrelas_min", type=float, default=0, location="args")
    query_params.add_argument("estrelas_max", type=float, default=0, location="args")
    query_params.add_argument("diaria_min", type=float, default=0, location="args")
    query_params.add_argument("diaria_max", type=float, default=0, location="args")
    query_params.add_argument("limit", type=int, default=0, location="args")
    query_params.add_argument("offset", type=int, default=0, location="args")
    query_params.add_argument("site_id", type=int, default=0, location="args")  # Adicione esta linha

    
    def get(self):
        filters = Hoteis.query_params.parse_args()
        query = HotelModel.query
        
        if filters["cidade"]:
            query = query.filter(HotelModel.cidade == filters["cidade"])
        if filters["estrelas_min"]:
            query = query.filter(HotelModel.estrelas >= filters["estrelas_min"])
        if filters["estrelas_max"]:
            query = query.filter(HotelModel.estrelas <= filters["estrelas_max"])
        if filters["diaria_min"]:
            query = query.filter(HotelModel.diaria >= filters["diaria_min"])
        if filters["diaria_max"]:
            query = query.filter(HotelModel.diaria <= filters["diaria_max"])
        if filters["limit"]:
            query = query.limit(filters["limit"])
        if filters["offset"]:
            query = query.offset(filters["offset"])
        if filters["site_id"]:
            query = query.offset(filters["site_id"])
        
        return {"hoteis": [hotel.json() for hotel in query]}

#Classe do elemento
class Hotel(Resource):
    #Argumentos usado para o padrão de criação (Devemos receber via Postman)
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="invalid empty '{}' field".format('name'))
    argumentos.add_argument('estrelas', type=float, required=True, help="invalid empty '{}' field".format('estrelas'))
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument("site_id",type=int, required=True, help="Evry hotel needs to be iliked with a site")

    #Metodo de requisição (GET)
    @jwt_required()
    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'Hotel not found'},404
    
    
    #Metodo de requisição (POST)
    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"messsage": "Hotel id '{}' already exists".format(hotel_id)}, 400
        
        dados = Hotel.argumentos.parse_args()        
        hotel = HotelModel(hotel_id, **dados)
        
        if not SiteModel.find_by_id(dados['site_id']):
            return {'message':'The hotel must be associated to a valid site id.' }, 400
            
        try:
            hotel.save_hotel()
        except:
            return {'message': 'An internal error ocurred trying to created hotel'}, 500
        return hotel.json()


    #Metodo de requisição (PUT)
    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args() 
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {'message': 'An internal error ocurred trying to save hotel'}, 500
        return hotel.json(), 201
    
    
    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
                return {'message': 'Hotel is deleted'}
            except:
                return {'message': 'An internal error ocurred trying to delete hotel'}, 500
        return {'message': 'Hotel not found'}, 404