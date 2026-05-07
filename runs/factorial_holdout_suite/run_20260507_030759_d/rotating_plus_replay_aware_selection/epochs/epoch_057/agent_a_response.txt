def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    def dist(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))  # king-move distance

    # Prefer resources we can likely win now; if none, choose move that reduces our distance most.
    best = (None, -10**18)
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        score = 0
        # slight bias to keep moving towards center-ish early, but deterministic
        if observation.get("turn_index", 0) < 10:
            score -= 0.05 * dist(nx, ny, (w - 1) / 2, (h - 1) / 2)

        # Evaluate best target under win-time margin
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            d_opp = dist(ox, oy, rx, ry)
            d_self = dist(nx, ny, rx, ry)
            # win margin: negative is good (we arrive sooner)
            margin = d_opp - d_self
            # reward immediate collection chance and being closer overall
            val = 0
            val += 3000 if (rx == nx and ry == ny) else 0
            if margin > 0:
                # we likely win: strongly reward margin and closeness after move
                val += 2000 + 80 * margin
                val -= 5 * d_self
            else:
                # if opponent likely wins, still help by lowering our distance; also allow "race" if tied
                val += (margin == 0) * 300
                val += -12 * (d_self - d_opp)  # prefer smaller d_self
                val -= 2 * d_self
            # extra tie-break: prefer resources with smaller sum distance
            val -= 0.1 * (d_self + d_opp)
            if val > local_best:
                local_best = val
        score += local_best
        # If resources are contested, discourage stepping into squares adjacent to our likely target that opponent can immediately steal
        # (simple deterministic nudge based on nearest opponent resource distance)
        nearest_r = None
        nd = 10**9
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            d = dist(ox, oy, rx, ry)
            if d < nd:
                nd = d
                nearest_r = (rx, ry)
        if nearest_r is not None:
            score -= 0.01 * dist(nx, ny, nearest_r[0], nearest_r[1])

        if score > best[1]:
            best = ((mdx, mdy), score)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]