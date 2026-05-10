def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))
    resources = list(observation.get("resources") or [])
    if not resources:
        return [0, 0]

    def nearest_dist(px, py):
        best = 10**9
        for rx, ry in resources:
            d = abs(rx - px) + abs(ry - py)
            if d < best:
                best = d
        return best

    my_now = nearest_dist(sx, sy)
    opp_now = nearest_dist(ox, oy)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            my_d = nearest_dist(nx, ny)
            improvement = (my_now - my_d)
            opp_d = opp_now
            tie_break = (opp_d - my_d)  # smaller my_d better, larger opp_d better
            candidates.append((improvement, tie_break, -abs(dx) - abs(dy), dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [candidates[0][3], candidates[0][4]]