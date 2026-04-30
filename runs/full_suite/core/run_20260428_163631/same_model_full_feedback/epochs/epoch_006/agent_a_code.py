def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # New policy (epoch 6 tweak): evaluate each possible one-step by its best "contest advantage",
    # but with an added anti-chase term to avoid repeatedly moving into opponent pressure.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # anti-stall/anti-opponent-pressure: prefer moving away from opponent slightly,
        # but still chase good contest positions.
        opp_dist = cheb(nx, ny, ox, oy)
        center_pen = abs(nx - cx) + abs(ny - cy)

        # If stepping onto/near a resource, strongly value it.
        step_value = -10**9
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # higher => after the move we're closer than opponent
            # emphasize immediate access: being exactly at resource is huge
            access = 0
            if nx == rx and ny == ry:
                access = 1000
            elif sd == 1:
                access = 40
            elif sd == 2:
                access = 10
            # discourage paths where opponent is already much closer (gap very negative)
            pressure = gap if gap > -100 else -200 - sd
            cand = gap * 20 + access + pressure
            if cand > step_value:
                step_value = cand

        # combine: maximize contest value, then keep distance from opponent moderately,
        # then move toward center for later maneuvering, then prefer small move.
        cand_key = (-(step_value), opp_dist, center_pen, abs(dx) + abs(dy), dx, dy)
        if best is None or cand_key < best[0]:
            best = (cand_key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]