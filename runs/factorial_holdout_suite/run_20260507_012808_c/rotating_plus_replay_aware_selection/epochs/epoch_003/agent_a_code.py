def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        # move toward center deterministically
        cx, cy = w // 2, h // 2
        best = min(moves, key=lambda m: dist((sx + m[0], sy + m[1]), (cx, cy)))
        return [best[0], best[1]]

    # Prefer resources we can reach at least as fast as opponent; otherwise best overall.
    def key_for_resource(r):
        rx, ry = r
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        return (d_self > d_opp, d_self - d_opp, d_self, rx, ry)

    reachable = [r for r in resources if dist((sx, sy), r) <= dist((ox, oy), r)]
    target = min(reachable, key=key_for_resource) if reachable else min(resources, key=key_for_resource)

    tx, ty = target

    # Choose our move that improves our distance and also (secondarily) maintains advantage vs opponent.
    def best_opp_next():
        opp_moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny):
                    opp_moves.append((dx, dy))
        if not opp_moves:
            return (ox, oy)
        # greedy toward target
        md = min(opp_moves, key=lambda m: dist((ox + m[0], oy + m[1]), (tx, ty)))
        return (ox + md[0], oy + md[1])

    nox, noy = best_opp_next()

    def move_score(m):
        nx, ny = sx + m[0], sy + m[1]
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((nox, noy), (tx, ty))
        # reduce our distance first; keep our advantage if possible; deterministic tie-break
        return (d_self, d_self - d_opp, abs(nx - tx) + abs(ny - ty), m[0], m[1])

    best_m = min(moves, key=move_score)
    return [best_m[0], best_m[1]]