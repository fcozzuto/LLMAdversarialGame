def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_val = -10**18

    # Choose a target resource (deterministically) then pick the move that improves our position vs it.
    candidates = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        d_me = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; break ties by closest to opponent then center bias.
        if d_me <= d_opp:
            candidates.append((d_opp, md(rx, ry, cx, cy), rx, ry, d_me))
    candidates.sort()
    if candidates:
        _, _, tx, ty, _ = candidates[0]
    else:
        # No contestable resources: drift toward center while avoiding getting worse.
        # Choose nearest valid resource to us; else center.
        nearest = None
        nd = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                d = md(sx, sy, rx, ry)
                if nd is None or d < nd or (d == nd and (rx, ry) < nearest):
                    nd = d
                    nearest = (rx, ry)
        if nearest:
            tx, ty = nearest
        else:
            tx, ty = cx, cy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = md(nx, ny, tx, ty)
        d_opp = md(ox, oy, tx, ty)
        # Score: minimize distance to target; also try to increase our lead (vs opponent) and keep safe from obstacles implicitly.
        lead = d_opp - d_me
        center = -md(nx, ny, cx, cy)
        opp_to_me = md(ox, oy, nx, ny)
        val = -d_me * 10 + lead * 5 + center * 1 - opp_to_me * 0.2
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]