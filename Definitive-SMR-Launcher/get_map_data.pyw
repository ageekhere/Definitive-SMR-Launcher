def get_map_data(map_id, matrix,return_type:str):
	if map_id in matrix[0]:
		i = matrix[0].index(map_id)
		if return_type == "id":
			return matrix[0][i]
		if return_type == "name":
			return matrix[1][i]
		if return_type == "url":
			return matrix[2][i]
		if return_type == "is_stable":
			return matrix[3][i]
		if return_type == "multiplayer":
			return matrix[4][i]
	return None