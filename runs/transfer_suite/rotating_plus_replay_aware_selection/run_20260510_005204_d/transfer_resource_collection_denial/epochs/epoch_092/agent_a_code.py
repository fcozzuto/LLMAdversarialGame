def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs_in = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_in:
        if p is None:
            continue
        try:
            px, py = p[0], p[1]
            obstacles.add((px, py))
        except Exception:
            pass

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    turns_remaining = observation.get("turns_remaining", 0)
    late = 1 if turns_remaining <= 6 else 0

    best_rx, best_ry = resources[0]
    best_score = -10**18
    limit = resources[:20]
    for rx, ry in limit:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        score = (d_op - d_me) * 1000 - d_me
        if late:
            score += 5000 if d_me == 0 else 0
        if score > best_score:
            best_score = score
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry
    best_m = [0, 0]
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_d or (d == best_d and [dx, dy] == [0, 0]):
            best_d = d
            best_m = [dx, dy]

    if best_m is None:
        return [0, 0]
    return best_m