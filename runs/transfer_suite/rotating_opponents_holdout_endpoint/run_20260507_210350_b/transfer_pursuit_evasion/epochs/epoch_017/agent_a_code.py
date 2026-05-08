def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role) or ("pursuit" in role)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_obs_dist(x, y):
        if not obstacles:
            return 99
        md = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < md:
                md = d
        return md

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Corner the opponent is closest to (evader_corner style)
    corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if pursuer:
            d_op = cheb(nx, ny, ox, oy)
            d_cor = cheb(nx, ny, corner[0], corner[1])
            md = min_obs_dist(nx, ny)
            # Prefer moving toward opponent's camp corner; then close distance; then keep away from obstacles
            key = (d_op, d_cor, -md, cheb(nx, ny, sx, sy))
        else:
            d_op = cheb(nx, ny, ox, oy)
            md = min_obs_dist(nx, ny)
            # Evade: maximize distance from opponent; also avoid obstacles slightly
            key = (-d_op, -md, cheb(nx, ny, sx, sy))
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]