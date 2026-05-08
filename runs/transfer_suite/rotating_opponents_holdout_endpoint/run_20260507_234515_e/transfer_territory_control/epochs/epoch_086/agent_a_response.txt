def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if unclaimed:
        candidates = unclaimed
    else:
        candidates = list(opp_terr) if opp_terr else [(ox, oy)]

    # Prefer targets closer by Manhattan, then prefer moving toward central area to fight territory_center_claim.
    def score_target(tx, ty):
        d = abs(sx - tx) + abs(sy - ty)
        center_bonus = abs(tx - cx) + abs(ty - cy)
        # If we can capture opponent territory immediately, value it more.
        cap_bonus = -1.2 if (tx, ty) in opp_terr else 0.0
        return d + 0.07 * center_bonus + cap_bonus

    primary = min(candidates, key=lambda t: (score_target(t[0], t[1]), t[0], t[1]))
    tx, ty = primary

    # Move selection: deterministic one-step look with obstacle avoidance and tie-breaking.
    def move_eval(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return (10**9,)
        # Main objective: reduce distance to target.
        dist = abs(nx - tx) + abs(ny - ty)
        # Secondary: if entering opponent territory, encourage capturing; avoid if we are likely blocked.
        enters_opp = 1 if (nx, ny) in opp_terr else 0
        # Tertiary: keep spreading our own territory (prefer unclaimed/our cells).
        enters_self = 1 if (nx, ny) in self_terr else 0
        unclaimed_here = 1 if (nx, ny) in set(unclaimed) else 0
        # Deterministic tie-break: smaller dx then dy.
        return (dist, -enters_opp, -unclaimed_here, -enters_self, dx, dy)

    best_dx, best_dy = 0, 0
    best_key = (10**9,)
    for dx, dy in moves:
        k = move_eval(dx, dy)
        if k < best_key:
            best_key = k
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]