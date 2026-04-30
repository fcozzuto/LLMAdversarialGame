def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Deterministic tie-break order: prefer diagonal/straight with smaller absolute delta, then dx, then dy
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]) * 10, d[0], d[1]))

    best_move = (0, 0)
    best_val = None

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Evaluate next position vs all resources: pick the move that maximizes our advantage and minimizes risk of being outpaced.
            val = -10**9
            for rx, ry in resources:
                dS_now = md(nx, ny, rx, ry)
                dO = md(ox, oy, rx, ry)
                adv = dO - dS_now  # positive means we are closer next step
                # Penalize moving away from closest "contested" resource while encouraging progress
                progress = -(dS_now * 2 + (abs((rx - nx)) + abs((ry - ny))) )
                # Prefer leaving ourselves on/near resources that are currently closer than opponent (adv>0)
                cont_bonus = 50 if adv > 0 else 0
                risk_penalty = -30 if adv < 0 else 0
                score = adv * 10 + progress + cont_bonus + risk_penalty
                if score > val:
                    val = score
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No visible resources: go toward the center deterministically (still obstacle-aware)
        cx, cy = W // 2, H // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = -md(nx, ny, cx, cy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]