def choose_move(observation):
    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            p = v.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return 0, 0

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = xy(o)
        obstacles.add((x, y))

    resources = [xy(r) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Choose the resource with maximum "advantage" (opponent distance minus self distance)
    best_t = None
    best_s = -10**18
    for tx, ty in resources:
        self_d = abs(tx - sx) + abs(ty - sy)
        opp_d = abs(tx - ox) + abs(ty - oy)
        adv = opp_d - self_d
        # Prefer strong advantage; break ties by smaller self distance, then deterministic coord order
        sc = adv * 1000 - self_d
        if sc > best_s or (sc == best_s and (self_d, tx, ty) < (abs(best_t[0]-sx)+abs(best_t[1]-sy), best_t[0], best_t[1])):
            best_s = sc
            best_t = (tx, ty)

    tx, ty = best_t

    # Move selection: evaluate all legal deltas by resulting distance to target,
    # plus a small term that discourages giving the opponent a closer path to target.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()  # deterministic tie-break

    best_m = (0, 0)
    best_h = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d_next = abs(tx - ox) + abs(ty - oy)
        # encourage moving closer to target; slight pressure if opponent is already too close
        h = self_d * 10 + (0 if (opp_d_next - self_d) <= 0 else 0) - (opp_d_next - self_d)
        if h < best_h or (h == best_h and (dx, dy) < best_m):
            best_h = h
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]