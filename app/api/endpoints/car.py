# import os
# import uuid
#
# from gosnomer import normalize
# from fastapi import APIRouter, Depends, UploadFile, Request
# from fastapi.responses import RedirectResponse
# from fastapi.templating import Jinja2Templates
# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette import status
# from aiofiles import open
#
#
# from app.core.config import settings
# from app.crud import car_crud, user_crud
# from app.schemas.car import CarCreate, CarDB, CarUpdate
# from app.core.db import get_async_session
# from app.api.validators import (
#     check_exist,
#     check_that_are_few_cars,
#     check_user_exist,
#     check_file_format,
#     check_user_by_tg_exist,
#     check_admin_or_myprofile_car,
#     check_car_unique,
# )
# from app.api.endpoints.guest import get_tg_id_cookie
#
#
# router = APIRouter(
#     prefix='/{user_id}/car',
#     tags=['car']
# )
#
# templates = Jinja2Templates(
#     directory='app/templates'
# )
#
#
# @router.get('/add')
# async def get_add_car_template(
#         request: Request,
#         user_id: int,
#         user_telegram_id: str = Depends(get_tg_id_cookie),
#         session: AsyncSession = Depends(get_async_session),
# ):
#     """Форма добавления машины"""
#     await check_admin_or_myprofile_car(
#         user_id=user_id,
#         user_telegram_id=int(user_telegram_id),
#         session=session,
#     )
#     return templates.TemplateResponse('car/add-car.html', {'request': request})
#
#
# @router.post(
#     '/add',
# )
# async def add_car(
#         request: Request,
#         user_id: int,
#         user_telegram_id: str = Depends(get_tg_id_cookie),
#         session: AsyncSession = Depends(get_async_session),
# ):
#     """Обработка формы создания машины. """
#     form_data = await request.form()
#     car = dict.fromkeys(['brand', 'model', 'license_plate_number', 'user_id'])
#     car['user_id'] = user_id
#     car['brand'] = form_data.get('brand')
#     car['model'] = form_data.get('model')
#     car['license_plate_number'] = form_data.get('license_plate_number')
#     await check_car_unique(
#         license_plate_number=car['license_plate_number'],
#         session=session
#     )
#     file = form_data.get('image')
#     user = await check_user_by_tg_exist(int(user_telegram_id), session)
#     await check_user_exist(user_id, session)
#     if not file.filename:
#         await car_crud.create_car(
#                     obj_in=CarCreate(**car),
#                     session=session,
#                     model='Car',
#                     user=user,
#                 )
#     else:
#         _, ext = os.path.splitext(file.filename)
#         imgdir: str = os.path.join(
#             settings.basedir, f'{settings.folder}/{user_id}')
#         if not os.path.exists(imgdir):
#             os.makedirs(imgdir)
#         content = await file.read()
#         check_file_format(file.content_type)
#         file_name = f'{uuid.uuid4().hex}{ext}'
#         async with open(os.path.join(imgdir, file_name), mode='wb') as f:
#             await f.write(content)
#         short_path = f'{settings.host_folder}/{user_id}/{file_name}'
#         if settings.local_test:
#             path_to_img = f'http://127.0.0.1:8000/{short_path}'
#         else:
#             path_to_img = f'http://{settings.host_ip}:{settings.app_port}/{short_path}'
#         await car_crud.create_car(
#             path=path_to_img,
#             obj_in=CarCreate(**car),
#             session=session,
#             model='Car',
#             user=user,
#         )
#     return RedirectResponse(
#         f'/user/profile/{user_id}',
#         status_code=status.HTTP_302_FOUND,
#     )
#
#
# @router.get('/{car_id}')
# async def get_edit_car_template(
#     car_id: int,
#     user_id: int,
#     request: Request,
#     user_telegram_id: str = Depends(get_tg_id_cookie),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     """Функция для получения формы редактирования машины. """
#     car = await car_crud.get(
#         obj_id=car_id,
#         session=session
#     )
#     await check_admin_or_myprofile_car(
#         user_id=user_id,
#         user_telegram_id=int(user_telegram_id),
#         session=session,
#         car=car,
#     )
#     return templates.TemplateResponse(
#         'car/edit-car.html',
#         {'request': request, 'car': car, 'user_id': user_id}
#     )
#
#
# @router.post('/{car_id}')
# async def edit_car(
#     request: Request,
#     car_id: int,
#     user_id: int,
#     user_telegram_id: str = Depends(get_tg_id_cookie),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     """Обработка формы для редактирования машины."""
#     db_car = await check_exist(car_crud, car_id, session)
#     form_data = await request.form()
#     car = dict.fromkeys(['brand', 'model', 'license_plate_number', 'car_id', 'image'])
#     car['car_id'] = car_id
#     car['brand'] = form_data.get('brand')
#     car['model'] = form_data.get('model')
#     car['license_plate_number'] = form_data.get('license_plate_number')
#     if not db_car.license_plate_number == normalize(
#             car['license_plate_number']):
#         await check_car_unique(
#             license_plate_number=car['license_plate_number'],
#             session=session
#         )
#     file = form_data.get('image')
#     user = await check_user_by_tg_exist(int(user_telegram_id), session)
#     await check_user_exist(user_id, session)
#     if file.filename:
#         _, ext = os.path.splitext(file.filename)
#         imgdir: str = os.path.join(
#             settings.basedir, f'{settings.folder}/{user_id}')
#         if not os.path.exists(imgdir):
#             os.makedirs(imgdir)
#         content = await file.read()
#         check_file_format(file.content_type)
#         file_name = f'{uuid.uuid4().hex}{ext}'
#         async with open(os.path.join(imgdir, file_name), mode='wb') as f:
#             await f.write(content)
#         short_path = f'{settings.host_folder}/{user_id}/{file_name}'
#         if settings.local_test:
#             path_to_img = f'http://127.0.0.1:8000/{short_path}'
#         else:
#             path_to_img = f'http://{settings.host_ip}:{settings.app_port}/{short_path}'
#         car['image'] = path_to_img
#     await car_crud.update(
#         db_obj=db_car,
#         obj_in=CarUpdate(**car),
#         session=session,
#         model='Car',
#         user=user,
#     )
#     return RedirectResponse(
#         f'/user/profile/{user_id}',
#         status_code=status.HTTP_302_FOUND,
#     )
#
#
# @router.get('/{car_id}/delete')
# async def get_edit_car_template(
#         request: Request,
#         car_id: int,
#         user_id: int,
#         user_telegram_id: str = Depends(get_tg_id_cookie),
#         session: AsyncSession = Depends(get_async_session),
# ):
#     """Функция для получения формы редактирования машины. """
#     errors = []
#
#     try:
#         car = await check_exist(car_crud, car_id, session)
#         await check_admin_or_myprofile_car(
#             user_id=user_id,
#             user_telegram_id=int(user_telegram_id),
#             session=session,
#             car=car,
#         )
#         await check_that_are_few_cars(user_id, session)
#         await car_crud.remove(
#             db_obj=car,
#             user=await check_user_by_tg_exist(int(user_telegram_id), session),
#             session=session,
#             model='Car',
#         )
#     except Exception as e:
#         errors.append(str(e))
#
#         return templates.TemplateResponse(
#             'car/edit-car.html',
#             {
#                 'request': request,
#                 'car': car,
#                 'user_id': user_id,
#                 'errors': errors,
#             }
#         )
#
#     return RedirectResponse(
#         f'/user/profile/{user_id}',
#         status_code=status.HTTP_302_FOUND,
#     )
