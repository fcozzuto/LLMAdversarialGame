def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): 
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return (dx*dx + dy*dy) ** 0.5
    # Choose a resource to contest: prefer closer than opponent
    best_res = None
    best_val = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles: 
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        val = sd - 0.9 * od
        if best_val is None or val < best_val - 1e-12 or (abs(val - best_val) <= 1e-12 and (rx, ry) < best_res):
            best_val = val
            best_res = (rx, ry)
    # If no resources, retreat toward center deterministically
    if best_res is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_res

    # Pick the best legal move by improving distance to target and preventing obstacle hits
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = dist((nx, ny), (tx, ty))
        # If target is current cell resource, staying is fine and best.
        # Also lightly discourage moving closer to opponent (defensive pressure).
        d_opp = dist((nx, ny), (ox, oy))
        score = d_self + 0.08 * (1.0 / (1.0 + d_opp))
        if best_score is None or score < best_score - 1e-12 or (abs(score - best_score) <= 1e-12 and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]