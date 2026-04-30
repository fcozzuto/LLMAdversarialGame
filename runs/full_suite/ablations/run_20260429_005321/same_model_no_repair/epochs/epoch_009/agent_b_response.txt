def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # BFS distances (short, capped) to handle obstacles deterministically
    def bfs(start, cap=14):
        if start in obstacles:
            return None
        dist = {start: 0}
        q = [start]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[(x, y)]
            if d >= cap:
                continue
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in dist:
                    dist[(nx, ny)] = d + 1
                    q.append((nx, ny))
        return dist

    sdmap = bfs((sx, sy))
    odmap = bfs((ox, oy))

    def cell_score(ns, no, rx, ry):
        # Prefer strictly earlier capture; otherwise still prefer lead and proximity.
        if ns is None:
            return -10**9
        if no is None:
            lead = 1 if ns >= 0 else -10**9
        else:
            lead = no - ns  # positive if we arrive earlier
        # Slight deterministic bias toward higher y (since agent_b starts near bottom in common maps)
        bias = (ry * 0.01) - (rx * 0.002)
        return lead * 10.0 + bias - ns * 0.15

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns_d = sdmap.get((nx, ny), None) if sdmap is not None else None

        # Evaluate best resource from this move
        move_best = -10**18
        for rx, ry in resources:
            # distance from current candidate to resource:
            # use precomputed sdmap where possible; if missing, approximate with Manhattan.
            ds = sdmap.get((rx, ry), None) if sdmap is not None else None
            # If ds is from current start, not candidate; compensate with local approximation:
            # Use Manhattan for candidate-to-resource if BFS-from-start doesn't include resource.
            if sdmap is None or ds is None:
                ds = abs(nx - rx) + abs(ny - ry)
            else:
                # estimate candidate-to-resource by manhattan but keep obstacle sensitivity via BFS near cap
                # (deterministic and cheap): candidate dist = BFS(current to res) - BFS(current to cand) if available
                dc = sdmap.get((nx, ny), None)
                if dc is not None:
                    ds = ds - dc
                else:
                    ds = abs(nx - rx) + abs(ny - ry)

            if odmap is None:
                do = abs(ox - rx) + abs(oy - ry)
            else:
                base = odmap.get((rx, ry), None)
                if base is None:
                    do = abs(ox - rx) + abs(oy - ry)
                else:
                    do = base

            s = cell_score(ds, do, rx, ry)
            if s > move_best:
                move_best = s

        # Add tie-break: prefer moves that reduce distance to the currently most contestable resource
        # (most likely to be taken by either agent)
        if move_best > best_val:
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]