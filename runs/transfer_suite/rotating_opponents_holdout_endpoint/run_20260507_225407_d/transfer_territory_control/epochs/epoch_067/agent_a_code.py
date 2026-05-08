def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    occ = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                occ.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cell_value(x, y):
        if (x, y) in unclaimed:
            return 120.0
        if (x, y) in opp_t:
            return 80.0
        return 0.0

    best_move = (0, 0)
    best_score = -10**18

    # If nothing to fight for, just creep toward center.
    targets = []
    if unclaimed:
        targets.append(("unclaimed", list(unclaimed)))
    if opp_t:
        targets.append(("opp", list(opp_t)))
    if not targets:
        best_move = (1 if sx < w - 1 else (-1 if sx > 0 else 0), 1 if sy < h - 1 else (-1 if sy > 0 else 0))
        return [int(best_move[0]), int(best_move[1])]

    # Use only a small set of closest targets for speed/determinism.
    cand_cells = []
    # Priority: unclaimed first, then opp territory.
    if unclaimed:
        near = sorted(unclaimed, key=lambda p: (abs(p[0]-cx)+abs(p[1]-cy), abs(p[0]-sx)+abs(p[1]-sy)))[:10]
        cand_cells.extend(near)
    if opp_t and len(cand_cells) < 10:
        near = sorted(opp_t, key=lambda p: (abs(p[0]-cx)+abs(p[1]-cy), abs(p[0]-sx)+abs(p[1]-sy)))[:10-len(cand_cells)]
        cand_cells.extend(near)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in occ:
            continue

        # Reward immediate value; encourage reducing distance to best candidate.
        imm = cell_value(nx, ny)

        # Distance reduction toward best candidate.
        best_red = -10**18
        for tx, ty in cand_cells:
            d0 = abs(sx - tx) + abs(sy - ty)
            d1 = abs(nx - tx) + abs(ny - ty)
            red = d0 - d1
            # Slightly prefer moves that approach center even when tied.
            center_bias = -(abs(nx - cx) + abs(ny - cy)) * 0.02
            v = cell_value(tx, ty)
            score = red * (1.0 + v / 200.0) + center_bias
            if score > best_red:
                best_red = score

        # Penalize stepping onto opponent territory unless it is on our way to the closest contested cell
        # (still allowed, but discourages random flipping).
        step_pen = -5.0 if (nx, ny) in opp_t and not unclaimed else 0.0
        total = imm * 0.9 + best_red * 3.0 + step_pen

        if total > best_score or (total == best_score and (dx, dy) < best_move):
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]