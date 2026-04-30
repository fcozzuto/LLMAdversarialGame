def choose_move(observation):
    W = observation.get("grid_width", 8) or 8
    H = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = observation.get("resources", []) or []
    valid_res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                valid_res.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_bias = 2 if (observation.get("remaining_resource_count", 0) or 0) <= 4 else 1
    # Prefer resources we can reach sooner than opponent; otherwise, contest high-value nearby targets.
    best_move = None
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if valid_res:
            local_best = -10**18
            for tx, ty in valid_res:
                our = man(nx, ny, tx, ty)
                opp = man(ox, oy, tx, ty)
                # If we are closer, score strongly; if not, discourage but still consider nearer contested targets.
                lead = (opp - our)
                val = lead * (10 + opp_bias) - our - 0.25 * (our + opp)
                # Encourage finishing near the resource.
                if our == 0:
                    val += 1000000
                local_best = val if val > local_best else local_best
            # Add small preference to move toward general direction between opponents to reduce opponent steals.
            mid_dir = (1 if ox > nx else -1 if ox < nx else 0, 1 if oy > ny else -1 if oy < ny else 0)
            contest = 0.5 * (abs(ox - nx) + abs(oy - ny)) * 0  # deterministic no-op placeholder avoided
            score = local_best + contest
        else:
            # No visible resources: move toward the center to be prepared.
            cx, cy = (W - 1) // 2, (H - 1) // 2
            score = -man(nx, ny, cx, cy)
        key = (score, -dx, -dy)  # deterministic tie-break
        if best_move is None or score > best_score or (score == best_score and key > (best_score, -best_move[0], -best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]