def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            sc = cheb((nx, ny), (tx, ty)) - 0.01 * cheb((nx, ny), (ox, oy))
            if best is None or sc < best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    resources_sorted = sorted(resources, key=lambda r: (r[0] * 9 + r[1]))
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self = dist((nx, ny), (0, 0))  # just to keep deterministic tie-breaking base
        best_adv = None
        best_self = None
        best_opp = None
        for r in resources_sorted:
            ds = dist((nx, ny), (r[0], r[1]))
            do = dist((ox, oy), (r[0], r[1]))
            adv = do - ds
            if best_adv is None or adv > best_adv or (adv == best_adv and (ds < best_self or (ds == best_self and r[0] + r[1] < best_opp))):
                best_adv = adv
                best_self = ds
                best_opp = r[0] + r[1]
        # Prefer grabbing resources where we get ahead; if behind, push to reduce our distance and increase opponent separation.
        sep = cheb((nx, ny), (ox, oy))
        own_to_best = best_self if best_self is not None else dist((nx, ny), (resources_sorted[0][0], resources_sorted[0][1]))
        val = (-best_adv, own_to_best, -sep, d_self, nx + ny)
        if best_move is None or val < best_move[0]:
            best_move = (val, dx, dy)

    return [best_move[1], best_move[2]]