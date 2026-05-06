def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obst)
    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for r in resources:
        our_d = md((sx, sy), r)
        opp_d = md((ox, oy), r)
        key = (our_d, -opp_d, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_target = r

    tx, ty = best_target
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        our_d = md((nx, ny), (tx, ty))
        opp_d = md((ox, oy), (tx, ty))
        step_score = (our_d, opp_d, nx == tx and ny == ty, dx, dy)
        if best_score is None or step_score < best_score:
            best_score = step_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]