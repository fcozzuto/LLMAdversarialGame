def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    if not resources:
        return [0, 0]

    # pick a target resource: closest to self, but discourage targets opponent is much closer to
    best = None
    best_score = -10**18
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # prefer smaller ds and relatively larger (do - ds)
        score = (-ds) + 0.75 * (do - ds)
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # choose the move that most improves target distance while keeping away from opponent and obstacles
    cur_ds = abs(tx - sx) + abs(ty - sy)
    cur_do = abs(ox - sx) + abs(oy - sy)
    best_m = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = abs(tx - nx) + abs(ty - ny)
        ndo = abs(ox - nx) + abs(oy - ny)

        # primary: reduce distance to target
        # secondary: if opponent is close, try to increase separation a bit
        val = (cur_ds - nds) + 0.2 * (ndo - cur_do)

        # slight tie-break: avoid moving into positions that are closer to opponent than to target
        if (abs(tx - nx) + abs(ty - ny)) > (abs(ox - nx) + abs(oy - ny)):
            val -= 0.05

        if val > best_val:
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]