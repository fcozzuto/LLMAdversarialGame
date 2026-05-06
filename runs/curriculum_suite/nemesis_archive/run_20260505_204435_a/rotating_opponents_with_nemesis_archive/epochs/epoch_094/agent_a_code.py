def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles_raw = observation.get("obstacles", []) or []
    resources_raw = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in resources_raw:
        x = y = None
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        if x is not None and inb(x, y) and (x, y) not in blocked:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]

    opp_d_center = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
        # Resource denial: choose moves that maximize how much closer we are than opponent for key resources.
        score = 0.0
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Bigger is better: advantage over opponent; slight preference for nearer resources.
            score += (d_opp - d_me) * 10.0 - d_me * 0.3
        # If very close to opponent, add term to avoid getting boxed by denying their nearest resource.
        if opp_d_center <= 2:
            score += (cheb(nx, ny, ox, oy) - opp_d_center) * 2.5
        # Deterministic tie-break: prefer moves that reduce our distance to best immediate advantage.
        if best_score is None or score > best_score or (score == best_score and cheb(nx, ny, resources[0][0], resources[0][1]) < cheb(sx, sy, resources[0][0], resources[0][1])):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]