from flask_restful import Resource
from models.site import SiteModel
from flask_jwt_extended import jwt_required
from resources.user_level import role_required

from resources.normalize import normalize_path_params

normalize_path_params()


class Sites(Resource):
    def get(self):
        return {'sites': [site.json() for site in SiteModel.query.all()]}
    
class Site(Resource):
    @jwt_required()
    def get(self, url):
        if url:
            site=SiteModel.find_site(url)
            if site:
                return site.json()
            return {'message': 'Site not found'}, 404
        else:
            sites = SiteModel.obter_todos_sites()
            sites_list = [site.json() for site in sites]
            return {'sites': sites_list}, 200
    
    @jwt_required()
    def post(self, url):
        if SiteModel.find_site(url):
            return{'message':'An site with this URL already exists'}, 400
        site = SiteModel(url)
        try:
            site.save_site()
        except:
            return{"message":"Error while creating the site."},500
        return site.json()
    
    @classmethod
    def obter_todos_sites(cls):
        return cls.query.all()      
    
    @jwt_required()
    @role_required(2,3)
    def delete(self, url):
        site = SiteModel.find_site(url)
        if site:
            site.delete_site()
            return {'message':'Site  deleted'}
        return {'messge': 'Site not found'}, 404
