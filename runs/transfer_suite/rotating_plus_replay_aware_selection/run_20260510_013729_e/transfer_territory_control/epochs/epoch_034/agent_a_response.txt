def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocks.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))
    seen = set()
    order = []
    for m in moves:
        if m not in seen:
            seen.add(m)
            order.append(m)
    # Deterministic priority tweak: prefer diagonals first, then straight, then stay
    order = sorted(order, key=lambda m: (m == (0, 0), 0 if (m[0] != 0 and m[1] != 0) else 1, abs(m[0]) + abs(m[1])))

    best = (-(10**18), (0, 0))
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocks:
            continue

        hscore = 0
        if (nx, ny) in opp_terr:
            hscore += 120
        elif (nx, ny) in unclaimed:
            hscore += 70
        elif (nx, ny) in self_terr:
            hscore += 5

        # Advance toward center and toward opponent, but avoid closing too much if opponent is on/near us
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        hscore += int(40 - 5 * dist_center)
        hscore += int(30 - 3 * dist_opp)

        # If likely to become surrounded by obstacles/opponent, prefer safer moves
        adj_blocks = 0
        adj_opp = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h:
                if (tx, ty) in blocks:
                    adj_blocks += 1
                if (tx, ty) in opp_terr:
                    adj_opp += 1
        hscore -= 6 * adj_blocks
        hscore -= 2 * adj_opp

        if hscore > best[0]:
            best = (hscore, (dx, dy))
    return [best[1][0], best[1][1]]