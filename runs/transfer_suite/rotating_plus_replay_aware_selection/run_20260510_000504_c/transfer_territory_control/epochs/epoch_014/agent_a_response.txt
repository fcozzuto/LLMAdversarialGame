def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation.get("opponent_position") or (sx, sy))
    ox, oy = opp_pos

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    cand_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cell_base_score(x, y):
        if (x, y) in opp_terr: return 12.0
        if (x, y) in unclaimed: return 5.0
        if (x, y) in self_terr: return 1.5
        return 0.2

    # Pick a deterministic target emphasizing close-to-opponent frontier captures
    if unclaimed:
        opp_cells = list(opp_terr) if opp_terr else [op for op in [(ox, oy)] if inb(op[0], op[1])]
        best_t = None
        best_key = None
        for (x, y) in unclaimed:
            if (x, y) in obstacles: 
                continue
            da = min(manh(x, y, px, py) for (px, py) in opp_cells) if opp_cells else manh(x, y, ox, oy)
            # Prefer cells that are (a) nearer to opponent frontier and (b) not too far from us
            db = manh(sx, sy, x, y)
            # Tie-break deterministically by coordinates
            key = (da, db, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (x, y)
        tx, ty = best_t
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = -1e18

    for dx, dy in cand_dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -1e17 if (dx != 0 or dy != 0) else -1e17  # will likely pick (0,0) if blocked
        else:
            step_score = cell_base_score(nx, ny)
            # Progress toward target
            before = manh(sx, sy, tx, ty)
            after = manh(nx, ny, tx, ty)
            progress = (before - after) * 2.5
            # Extra incentive to enter cells adjacent to opponent territory (frontline pressure)
            adj_opp = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0: 
                        continue
                    q = (nx + ddx, ny + ddy)
                    if inb(q[0], q[1]) and q in opp_terr:
                        adj_opp = 1
            frontier_bonus = 4.0 if adj_opp else 0.0
            # Avoid getting stuck in already-controlled self territory if it doesn't help progress
            self_pen = -0.3 if (nx, ny) in self_terr and progress <= 0 else 0.0
            val = step_score + progress + frontier_bonus + self_pen
        # Deterministic tie-break: prefer smaller dx, then smaller dy
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]