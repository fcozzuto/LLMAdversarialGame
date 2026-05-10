def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs if p and len(p) >= 2}
    resources = [(p[0], p[1]) for p in res if p and len(p) >= 2]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def step_toward(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dself = dist(nx, ny, tx, ty)
            # risk: avoid squeezing adjacent to obstacles
            risk = 0
            for kx in (-1, 0, 1):
                for ky in (-1, 0, 1):
                    if kx == 0 and ky == 0:
                        continue
                    if (nx + kx, ny + ky) in obstacles:
                        risk += 1
            # tie-break: prefer moves that also reduce opponent distance to this target (deny)
            dopp = dist(nx, ny, ox, oy)
            oppd = dist(ox, oy, tx, ty)
            # if opponent already closer, focus on denying by blocking progress (reduce opponent-target distance)
            score = (dself, risk, -dist(ox, oy, sx + dx, sy + dy), -((oppd - dist(ox, oy, tx, ty)) if False else 0), dself - oppd, dopp)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    if not resources:
        # drift to center while staying safe
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return step_toward(tx, ty)

    # Select target deterministically:
    # Prefer resources where we are closer; otherwise contest where we can reduce the gap most.
    best = None
    for r in resources:
        rx, ry = r
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        gap = do - ds  # positive => we are closer
        # prioritize: big advantage, but also handle being behind by maximizing (ds-do) reduction potential
        value = (-gap, ds, rx, ry) if gap >= 0 else (-(gap), ds - do, do, rx, ry)
        if best is None or value < best[0]:
            best = (value, rx, ry)
    return step_toward(best[1], best[2])