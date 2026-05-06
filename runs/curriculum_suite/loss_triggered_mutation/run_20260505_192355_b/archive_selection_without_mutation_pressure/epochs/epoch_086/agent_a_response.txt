def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    # Pick a target that maximizes advantage, but also discourage stepping toward opponent.
    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_t = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        # advantage: how much closer we are than opponent
        adv = (opp_d - self_d) * 3 - md(rx, ry, w - 1 - sx, h - 1 - sy) * 0
        # tie-break deterministically: prefer lower y then lower x (stable)
        if adv > best_adv or (adv == best_adv and (ry, rx) < (best_t[1], best_t[0])):
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_m = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_to_t = md(nx, ny, tx, ty)
        opp_to_t = md(ox, oy, tx, ty)

        # Also compute our step advantage over opponent on the target.
        adv = (opp_to_t - self_to_t)

        # Opponent pressure: keep distance from opponent to reduce interference with sweep.
        self_to_opp = md(nx, ny, ox, oy)
        opp_to_self = md(ox, oy, nx, ny)
        opp_pressure = self_to_opp - opp_to_self  # equals 0, but keep form deterministic

        # Secondary: maximize how much we increase separation from opponent while not worsening target too much.
        sep_score = self_to_opp

        # Tertiary: deterministically prefer moves that go to lower (y,x) among equal scores.
        sc = adv * 10 + sep_score * 0.5 - self_to_t * 0.1 + opp_pressure * 0.0
        if sc > best_sc or (sc == best_sc and (ny, nx) < (best_m[1] + sx, best_m[0] + sx)):
            best_sc = sc
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]