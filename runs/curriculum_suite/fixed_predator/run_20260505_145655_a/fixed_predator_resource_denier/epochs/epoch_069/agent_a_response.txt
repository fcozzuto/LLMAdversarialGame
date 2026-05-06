def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: prefer resources where we can deny (opponent closer than us), then nearer.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Larger when opponent is closer, and avoid very far targets.
        val = (od - sd) * 10 - sd - 0.2 * (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        if best is None or val > best[0]:
            best = (val, rx, ry)
    tx, ty = best[1], best[2]

    # Move choice: reduce distance to target and try to avoid becoming closer to opponent than necessary.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_from_t_after = man(sx, sy, tx, ty) - d_to_t
        # If we can also increase opponent's distance to the target (soft denial), favor it.
        d_opp_to_t = man(ox, oy, tx, ty)
        d_opp_to_t_after = d_opp_to_t  # opponent doesn't move; keep as reference
        # Encourage staying between opponent and target when possible by increasing our distance to opponent.
        d_between = man(nx, ny, ox, oy)
        score = d_from_t_after * 3 + d_between * 0.06 - d_to_t * 0.15
        # Mildly penalize moves that let opponent be closer to target than us by a lot.
        sd_here = d_to_t
        od_here = d_opp_to_t_after
        score -= max(0, od_here - sd_here - 1) * 0.25
        if best_m is None or score > best_m[0]:
            best_m = (score, dx, dy)

    if best_m is None:
        return [0, 0]
    dx, dy = best_m[1], best_m[2]
    return [int(dx), int(dy)]