def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if unclaimed:
            nearest = None
            for p in unclaimed:
                px, py = p
                d = (px - nx) * (px - nx) + (py - ny) * (py - ny)
                if nearest is None or d < nearest:
                    nearest = d
            score = -nearest
        else:
            score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        score -= 0.05 * dist2((nx, ny), (ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]