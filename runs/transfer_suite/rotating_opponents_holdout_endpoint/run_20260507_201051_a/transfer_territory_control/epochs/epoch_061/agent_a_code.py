def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or observation.get("unclaimed") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (-1, -1), (1, 1), (-1, 1)]
    best = -10**9
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            val = -100000
        else:
            dist_u = 99
            for ux, uy in unclaimed:
                d = manh(nx, ny, ux, uy)
                if d < dist_u:
                    dist_u = d
            val = 0
            if (nx, ny) in unclaimed:
                val += 120 - dist_u
            if (nx, ny) in selfT:
                val += 10
            val += 5 * manh(nx, ny, ox, oy)  # prefer moving away from opponent
        if val > best:
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]