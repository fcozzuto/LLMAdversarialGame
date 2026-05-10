def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in blocked:
                unclaimed.append((x, y))

    # If nothing to expand, drift to safer corner opposite opponent.
    if not unclaimed:
        tx, ty = (0, 0) if (ox + oy) > (W - 1 - ox + H - 1 - oy) else (W - 1, H - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        for cdx, cdy in cand:
            nx, ny = sx + cdx, sy + cdy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in blocked:
                return [cdx, cdy]
        return [0, 0]

    # Territory_counterclaim: bias targets far from opponent to avoid easy counterclaims.
    # Prefer unclaimed that increases distance from opponent.
    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_dists = [(md(tx, ty, ox, oy), -md(sx, sy, tx, ty), -((tx - (W - 1) / 2.0) ** 2 + (ty - (H - 1) / 2.0) ** 2), tx, ty) for (tx, ty) in unclaimed]
    # Sort deterministically by (farther from opponent, closer to us)
    unclaimed.sort(key=lambda t: (-md(t[0], t[1], ox, oy), md(sx, sy, t[0], t[1]), t[0], t[1]))
    tx, ty = unclaimed[0]

    # Evaluate possible moves with simple deterministic heuristic + obstacle avoidance.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in blocked:
            continue
        # Score: get closer to target, also keep farther from opponent, slight center bias.
        us_to_target = md(nx, ny, tx, ty)
        op_to_target = md(nx, ny, ox, oy)
        center_bias = -((nx - (W - 1) / 2.0) ** 2 + (ny - (H - 1) / 2.0) ** 2) * 0.01
        # Encourage moving to unclaimed (even if flipping allowed, it should be advantageous to claim).
        in_unclaimed = 1 if (nx, ny) in set(unclaimed[:64]) else 0
        score = (-us_to_target) + (op_to_target * 0.3) + center_bias + (in_unclaimed * 2.0) - (abs(dx) + abs(dy)) * 0.02
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]