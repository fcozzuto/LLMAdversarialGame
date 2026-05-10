def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation.get("opponent_position") or [w - 1, h - 1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj8(a, b):
        return abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1 and (a[0], a[1]) != (b[0], b[1])

    # Prioritize unclaimed cells that are adjacent to opponent territory (likely to flip/control race).
    border_unclaimed = []
    for c in unclaimed:
        for ot in opp_terr:
            if abs(c[0] - ot[0]) <= 1 and abs(c[1] - ot[1]) <= 1:
                border_unclaimed.append(c)
                break

    # If no direct border target, bias toward opponent position while keeping to unclaimed/edge cells.
    if border_unclaimed:
        targets = border_unclaimed
    else:
        unclaimed_list = list(unclaimed)
        edge_targets = [c for c in unclaimed_list if c[0] in (0, w - 1) or c[1] in (0, h - 1)]
        targets = edge_targets or unclaimed_list

    if not targets:
        targets = [opp_pos]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick best neighbor cell by heuristic score.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        val = 0.0
        if cell in unclaimed:
            val += 3.8
        if cell in self_terr:
            val += 0.8
        if cell in opp_terr:
            val += 3.1  # entering opponent territory flips control

        # Strongly favor stepping toward border-unclaimed targets.
        if targets:
            # compute closest target distance; keep cheap by local min over up to 12 closest targets
            tnear = sorted(targets, key=lambda t: man(t, cell))
            d = man(tnear[0], cell)
            val += 2.6 / (1 + d)

        # Avoid wandering by penalizing stepping away from opponent and from self toward center
        val += -0.15 * man(cell, opp_pos)
        val += -0.05 * (abs(cell[0] - (w // 2)) + abs(cell[1] - (h // 2)))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]