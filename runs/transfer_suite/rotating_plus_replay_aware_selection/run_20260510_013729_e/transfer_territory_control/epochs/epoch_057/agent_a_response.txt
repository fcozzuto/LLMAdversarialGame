def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    targets = list(unclaimed) if unclaimed else []
    if not targets:
        for p in observation.get("resources") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
    if not targets:
        targets = [((w - 1) // 2, (h - 1) // 2)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    prefer = 1 if (int(observation.get("turn_index") or 0) % 2 == 0) else 0

    best = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        md_un = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        md_opp = abs(nx - ox) + abs(ny - oy)

        cell = (nx, ny)
        cell_bonus = 0
        if cell in unclaimed:
            cell_bonus += 12
        if cell in opp_t:
            cell_bonus += 6 + (2 if md_un <= 2 else 0)
        if cell in self_t:
            cell_bonus += 2

        # Edge pressure: keep pushing outward deterministically
        edge_bonus = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_bonus = 3

        val = (cell_bonus + edge_bonus) * 100 - md_un * 10 + md_opp * 1
        tie = (0 if (dx, dy) == (0, 0) else 1) + (1 if prefer == 0 and dx < 0 else 0)  # deterministic tiebreaker

        if best is None or val > best[0] or (val == best[0] and tie < best[2]) or (val == best[0] and tie == best[2] and (dx, dy) < best[1]):
            best = (val, (dx, dy), tie)

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]