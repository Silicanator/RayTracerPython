import numpy as np 
import matplotlib.pyplot as plt 

def normalize(vector):
	return vector/np.linalg.norm(vector)

def sphere_intersect(center, radius, ray_origin, ray_direction):
	b = 2 * np.dot(ray_direction, ray_origin-center)
	c = np.linalg.norm(ray_origin-center) ** 2 - radius ** 2
	delta = b **2 - 4*c
	if delta > 0:
		t1 = (-b + np.sqrt(delta))/2
		t2 = (-b - np.sqrt(delta))/2
		if t1>0 and t2>0:
			return min(t1, t2)
	return None

def nearest_intersected_object(objects, ray_origin, ray_direction):
    distances = [sphere_intersect(obj['center'], obj['radius'], ray_origin, ray_direction) for obj in objects]
    nearest_object = None
    min_distance = np.inf
    for index, distance in enumerate(distances):
        if distance and distance < min_distance:
            min_distance = distance
            nearest_object = objects[index]
    return nearest_object, min_distance

width = 200
height = 300

camera=np.array([0,0,1])
ratio = float(width)/height
screen = (-1, 1/ratio, 1, -1/ratio)

image=np.zeros((height, width, 3))

objects = [
{'center': np.array([0.4,0.2,-1]), 'radius':0.7, 'ambient': np.array([0.1,0,0]), 'diffuse': np.array([0.7,0,0]), 'specular': np.array([1,1,1]), 'shininess': 100}
]

light = {'position': np.array([-3,3,5]), 'ambient': np.array([1,1,1]), 'diffuse': np.array([1,1,1]), 'specular': ([1,1,1])}

for i, y in enumerate(np.linspace(screen[1],screen[3],height)):
	for j, x in enumerate(np.linspace(screen[0],screen[2],width)):

		#image[i,j] = 

		origin = camera
		pixel = np.array([x,y,0])
		direction = normalize(pixel-origin)

		nearest_object, min_distance = nearest_intersected_object(objects, origin, direction)

		if nearest_object is None:
			continue

		intersection = origin + min_distance * direction
		normal_to_intersection = normalize(intersection-nearest_object['center'])
		shifted_point = intersection + 1e-5 * normal_to_intersection
		intersection_to_light = normalize(light['position']-shifted_point)
		intersection_to_light_distance = np.linalg.norm(light['position']-shifted_point)
		_,min_distance = nearest_intersected_object(objects,shifted_point,intersection_to_light)
		is_shadowed = min_distance < intersection_to_light_distance

		if is_shadowed:
			continue

		illumination = np.zeros((3))

		illumination += nearest_object['ambient'] * light['ambient']

		# diffuse
		illumination += nearest_object['diffuse'] * light['diffuse'] * np.dot(intersection_to_light, normal_to_intersection)

		# specular
		intersection_to_camera = normalize(camera - intersection)
		H = normalize(intersection_to_light + intersection_to_camera)
		illumination += nearest_object['specular'] * light['specular'] * np.dot(normal_to_intersection, H) ** (nearest_object['shininess'] / 4)

		image[i, j] = np.clip(illumination, 0, 1)

	print("progress: %d/%d" % (i+1, height))

plt.imsave('image.png',image)
