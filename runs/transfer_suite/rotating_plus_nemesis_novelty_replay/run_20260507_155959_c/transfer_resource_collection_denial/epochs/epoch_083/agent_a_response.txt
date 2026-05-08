def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    moves.append((0, 0))

    if not resources:
        # Go to nearest corner away from opponent's quadrant
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Consider closest resources to self to keep deterministic and fast
    res_sorted = sorted(resources, key=lambda r: (abs(r[0] - sx) + abs(r[1] - sy), r[0], r[1]))
    res_sorted = res_sorted[:10]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_val = -10**18

    # Heuristic: maximize lead on the "most contestable" resource after our move.
    # Also slightly prefer moving into the center lines relative to opponent to counter row sweeps.
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0
    opp_row = oy
    opp_col = ox

    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        # Evaluate best margin among candidate resources
        best_margin = -10**18
        for rx, ry in res_sorted:
            sd = man(nsx, nsy, rx, ry)
            od = man(ox, oy, rx, ry)
            margin = od - sd  # positive means we're closer
            # Small tie-break: prefer resources not on opponent's current row/col (helps vs sweep_rows)
            anti_sweep = 0
            if ry == opp_row:
                anti_sweep -= 0.25
            if rx == opp_col:
                anti_sweep -= 0.25
            # Slightly bias toward center to avoid being herded into edges by sweep patterns
            center_bias = -0.01 * (abs(rx - center_x) + abs(ry - center_y))
            val = margin + anti_sweep + center_bias
            if val > best_margin:
                best_margin = val

        # Additional preference for progressing toward any resource (avoid indecisive dithering)
        progress = min(man(nsx, nsy, rx, ry) for rx, ry in res_sorted)
        # Combine (higher margin better; lower progress better)
        score = best_margin * 10.0 - progress
        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]