def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def norm_point(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                return int(p["position"][0]), int(p["position"][1])
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return None

    obs = set()
    for p in obstacles:
        q = norm_point(p)
        if q is not None:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        q = norm_point(p)
        if q is not None:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    on_resource = (sx, sy) in set(res)
    if on_resource:
        return [0, 0]

    # Evaluate a move by how much it improves relative advantage on the best remaining resource.
    res_set = set(res)
    def best_adv(px, py):
        best = None
        for tx, ty in res:
            if (tx, ty) not in res_set:
                continue
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Bias to take resources that opponent cannot reach quickly; add slight tie-break for self closeness.
            adv = (od - sd * 12 - 0.1 * (sd == 0))  # deterministic float not required; still deterministic
            key = (adv, -sd, tx, ty)
            if best is None or key > best[0]:
                best = (key, (tx, ty), sd, od)
        return best[0] if best else (-10**9, 0, 0, 0)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic order: prefer staying only if equal.
    moves_sorted = sorted(moves, key=lambda d: (d[0], d[1]))
    cand = None
    for dx, dy in moves_sorted:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        score = best_adv(nx, ny)
        if cand is None or score > cand[0]:
            cand = (score, dx, dy)

    if cand is None:
        return [0, 0]
    return [int(cand[1]), int(cand[2])]