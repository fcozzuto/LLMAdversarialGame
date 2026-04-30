def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # If no resources, move to maximize distance from opponent while avoiding obstacles
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Pick best target by winning "race" against opponent: maximize (d_opp - d_self)
    if resources:
        best_res = None
        best_adv = -10**9
        best_dself = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dself = dist((sx, sy), (rx, ry))
            dopp = dist((ox, oy), (rx, ry))
            adv = dopp - dself
            if adv > best_adv or (adv == best_adv and dself < best_dself):
                best_adv = adv; best_dself = dself; best_res = (rx, ry)
        tx, ty = best_res
    else:
        tx, ty = sx, sy

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if resources:
            d_to_target = dist((nx, ny), (tx, ty))
            d_from_opp = dist((nx, ny), (ox, oy))
            # Encourage reaching target while staying away from opponent; small bias for progress
            score = (d_from_opp * 0.35) - (d_to_target) + (best_adv * 0.01)
        else:
            d_from_opp = dist((nx, ny), (ox, oy))
            score = d_from_opp * 1.0 - (abs(nx - (w-1)) + abs(ny - (h-1))) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]