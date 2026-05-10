def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obs_set.add((int(p["position"][0]), int(p["position"][1])))
            elif "x" in p and "y" in p:
                obs_set.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs_set

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # choose the resource that gives the best "race" after this move
        cur_best = None
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # maximize (opp_distance - self_distance); tie favor faster self, then smaller resource coord deterministically
            val = (od - sd, -sd, -rx, -ry)
            if cur_best is None or val > cur_best:
                cur_best = val
        if cur_best is None:
            continue
        if best_val is None or cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]