def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs if p is not None and len(p) >= 2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves += [(0, 0)]
    moves.sort(key=lambda t: (t[0] == 0 and t[1] == 0, abs(t[0]) + abs(t[1]), t[0], t[1]))

    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = abs(nx - ox) + abs(ny - oy)
            best = min(best, (d, dx * 0 + abs(dx) + abs(dy), dx, dy))
    return [best[2], best[3]]