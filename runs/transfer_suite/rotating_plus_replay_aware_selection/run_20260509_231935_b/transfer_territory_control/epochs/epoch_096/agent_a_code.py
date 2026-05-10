def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obs

    un_list = observation.get("unclaimed_cells") or []
    tgt_un = []
    for p in un_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            tgt_un.append((int(p[0]), int(p[1])))

    opp_t = observation.get("opponent_territory") or []
    opp_set = set()
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    dirs2 = [(dx, dy, man(sx + dx, sy + dy, ox, oy)) for dx, dy in dirs if legal(sx + dx, sy + dy)]
    dirs2.sort(key=lambda t: (t[2], t[0], t[1]))
    best = None
    best_val = None

    tgts = tgt_un if tgt_un else list(opp_set)
    if not tgts:
        return [0, 0]

    for dx, dy, _ in dirs2:
        nx, ny = sx + dx, sy + dy
        d_best_un = min(man(nx, ny, tx, ty) for tx, ty in tgts)
        captures_opp = 1 if (nx, ny) in opp_set else 0
        is_unclaimed = 1 if (nx, ny) in set(tgt_un) else 0
        # Prefer capturing, then expanding into unclaimed; otherwise advance toward nearest target.
        val = (-10 * captures_opp) + (-3 * is_unclaimed) + (d_best_un)
        # Tie-break deterministically by preferring moves that reduce distance to opponent.
        val2 = val * 1000 + man(nx, ny, ox, oy)
        if best_val is None or val2 < best_val:
            best_val = val2
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]