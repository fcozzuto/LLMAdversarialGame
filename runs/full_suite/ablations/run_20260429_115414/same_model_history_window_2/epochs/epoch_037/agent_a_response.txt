def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Prefer states where we are likely to reach a resource earlier than opponent.
        # Score combines: lead over opponent, closeness to resources, and distance from opponent.
        lead_term = 0
        dist_term = 0
        opp_term = -cheb(nx, ny, ox, oy)

        for i, (rx, ry) in enumerate(resources[:12]):
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            lead = d_op - d_me  # positive if we are closer
            # Deterministic tie-break: slight bias by resource index.
            s = 2.5 * lead - 0.25 * d_me + 0.01 * (len(resources) - i)
            if s > lead_term:
                lead_term = s
            if i == 0:
                dist_term = -0.01 * d_me

        score = lead_term + dist_term + 0.05 * opp_term

        # If resource set is empty, just move to maximize distance from opponent (safer scoring profile).
        if not resources:
            score = opp_term

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]