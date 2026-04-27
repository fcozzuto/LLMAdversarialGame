def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    if resources:
        best_res = None
        best_adv = -10**9
        min_self = 10**9
        min_opp = 10**9
        for r in resources:
            dS = dist((sx, sy), r)
            dO = dist((ox, oy), r)
            if dS < min_self: min_self = dS
            if dO < min_opp: min_opp = dO
            adv = dO - dS
            if adv > best_adv or (adv == best_adv and (dS < dist((sx, sy), best_res)) if best_res else True):
                best_adv = adv
                best_res = r
        target = best_res
        behind = (min_self - min_opp) > 0
    else:
        target = (w//2, h//2)
        behind = False

    best_move = (0, 0)
    best_cost = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dT = dist((nx, ny), target)
        dO = dist((nx, ny), (ox, oy))
        cost = dT
        cost += 0.03 * dO * (1 if not behind else -1)
        if resources and dist((nx, ny), target) == 0:
            cost -= 5
        if cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]