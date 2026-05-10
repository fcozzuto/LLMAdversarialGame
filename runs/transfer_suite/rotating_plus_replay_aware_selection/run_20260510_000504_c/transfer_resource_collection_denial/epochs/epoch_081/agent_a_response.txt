def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    def parse_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                q = p["position"]
                return int(q[0]), int(q[1])
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return None

    obs_set = set()
    for p in obstacles:
        q = parse_pos(p)
        if q is not None:
            obs_set.add(q)

    res_list = []
    for r in resources:
        q = parse_pos(r)
        if q is not None:
            res_list.append(q)
    if not res_list:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target that we can reach earlier than opponent (or at least maximally deny).
    best = None
    best_key = None
    for rx, ry in res_list:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd)  # maximize advantage, then minimize our distance
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    # Prefer moves that get closer to target and avoid obstacles (including tentative next cell).
    cur_d = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        nd = cheb(nx, ny, tx, ty)
        # score: primarily minimize distance; secondarily keep relative advantage vs opponent.
        no_adv = (cheb(ox, oy, tx, ty) - nd)
        score = (-nd, -no_adv, abs(dx) + abs(dy) == 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all safe moves were blocked, stay (engine will keep position).
    if best_score is None:
        return [0, 0]

    # If staying is already best, return it.
    if cheb(sx, sy, tx, ty) <= min(best_score[0] * -1, cur_d):
        return best_move
    return best_move