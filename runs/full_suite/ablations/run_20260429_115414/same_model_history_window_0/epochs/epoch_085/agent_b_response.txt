def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox0, oy0 = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for king moves

    if not resources:
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in resources:
        sd = dist((x0, y0), (rx, ry))
        od = dist((ox0, oy0), (rx, ry))
        val = (od - sd) * 100 - sd  # prefer resources where we're relatively closer
        if best is None or val > best_val or (val == best_val and (rx, ry) < best):
            best = (rx, ry)
            best_val = val
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic preference: moves that reduce distance to target, then lexicographic order
    best_move = (0, 0)
    best_md = None
    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        md = dist((nx, ny), (tx, ty))
        if best_md is None or md < best_md or (md == best_md and (dx, dy) < best_move):
            best_md = md
            best_move = (dx, dy)

    if best_md is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]