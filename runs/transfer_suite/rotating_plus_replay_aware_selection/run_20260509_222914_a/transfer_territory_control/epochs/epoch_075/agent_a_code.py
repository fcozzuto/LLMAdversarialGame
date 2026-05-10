def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)
    self_ter = set(tuple(p) for p in observation.get("self_territory") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in observation.get("opponent_territory") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)

    # Candidate targets: unclaimed cells that are adjacent to opponent territory (frontier), else all unclaimed.
    frontier = set()
    for (x, y) in opp_ter:
        for dx, dy in dirs[1:]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                frontier.add((nx, ny))
    targets = frontier if frontier else unclaimed

    # If immediate capture exists, prioritize it strongly.
    best_imm = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in opp_ter:
            best_imm = (dx, dy)
            break
    if best_imm is not None:
        return [best_imm[0], best_imm[1]]

    # Deterministic best move by heuristic: immediate cell value + distance to best target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in self_ter:
            val += 2
        elif (nx, ny) in unclaimed:
            val += 8
        elif (nx, ny) in opp_ter:
            val += 30  # should be unreachable due to immediate capture check, but safe

        # Distance to nearest target, with tie-break favoring moves that reduce Manhattan distance to opponent territory.
        if targets:
            md = None
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if md is None or d < md:
                    md = d
            val += -2 * md
        else:
            # fallback: drift toward board center
            val += -(abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]