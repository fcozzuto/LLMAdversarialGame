def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Pick nearest resource; if none, move toward opponent.
    target = None
    res = observation.get("resources", None)
    res_list = []
    if isinstance(res, list):
        for r in res:
            if isinstance(r, dict):
                if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                    res_list.append((int(r["position"][0]), int(r["position"][1])))
                elif "x" in r and "y" in r:
                    res_list.append((int(r["x"]), int(r["y"])))
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                res_list.append((int(r[0]), int(r[1])))
    if res_list:
        bestd = 10**9
        for x, y in res_list:
            d = cheb(sx, sy, x, y)
            if d < bestd:
                bestd, target = d, (x, y)
    if target is None:
        target = (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 10**9, 0, 0)  # (dist, risk, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, target[0], target[1])
        # risk: prefer moving away from opponent when no resources exist? Use opponent distance as tie-break.
        oppd = cheb(nx, ny, ox, oy)
        cand = (d, -oppd, dx, dy)
        if cand[0] < best[0] or (cand[0] == best[0] and cand[1] < best[1]) or (cand[0] == best[0] and cand[1] == best[1] and (cand[2], cand[3]) < (best[2], best[3])):
            best = cand
    dx, dy = int(best[2]), int(best[3])
    if not ok(sx + dx, sy + dy):
        # Fallback to any valid move (deterministic).
        for dx2, dy2 in moves:
            if ok(sx + dx2, sy + dy2):
                return [int(dx2), int(dy2)]
        return [0, 0]
    return [dx, dy]