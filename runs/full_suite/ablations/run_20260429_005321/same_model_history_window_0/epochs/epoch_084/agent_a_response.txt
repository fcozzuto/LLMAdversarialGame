def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # Choose a contested resource to aim at: minimize (my_dist - opp_dist) => most winnable
    best_target = None
    best_key = None
    for r in resources:
        d1 = dist((sx, sy), r)
        d2 = dist((ox, oy), r)
        key = d1 - d2
        if best_key is None or key < best_key or (key == best_key and (d1 < dist((sx, sy), best_target))):
            best_key = key
            best_target = r
    if best_target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(ox - tx) + abs(oy - ty)
        # Prefer getting closer to target while not letting opponent improve; also slightly avoid proximity to opponent
        score = 1000 - my_d * 20 + (my_d - opp_d) * 5 - dist((nx, ny), (ox, oy))
        # Extra bias toward resources if we're near any: move to nearest resource cell
        if resources:
            mr = min(dist((nx, ny), r) for r in resources)
            score += (15 - mr) * 3
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]