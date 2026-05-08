def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    def dist(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))

    if unclaimed:
        candidates = unclaimed
    else:
        candidates = []
        for x in range(w):
            for y in range(h):
                if (x, y) not in obstacles and (x, y) not in self_terr and (x, y) not in opp_terr:
                    candidates.append((x, y))
        if len(candidates) > 40:
            candidates.sort(key=lambda c: dist((w // 2, h // 2), c))
            candidates = candidates[:40]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    def objective(cell):
        # Prefer fast progress from us, deny opponent by staying far from them.
        dv = -dist((sx, sy), cell) + 0.85 * dist((ox, oy), cell)
        # Small center bias to hold territory.
        dv += 0.08 * (-(abs(cell[0] - (w - 1) / 2) + abs(cell[1] - (h - 1) / 2)))
        # Prefer attacking unclaimed rather than marching into their territory.
        if cell in unclaimed:
            dv += 0.25
        if cell in opp_terr:
            dv -= 0.15
        return dv

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = None
        if (nx, ny) in self_terr:
            # Staying within our territory is safe; still push toward best nearby.
            val = objective((nx, ny))
        else:
            # Evaluate the best candidate after taking this step.
            # Deterministic and cheap: compare nearby candidate set by distance from next pos.
            nextpos = (nx, ny)
            # If unclaimed small, just compute directly.
            if len(candidates) <= 25:
                val = -dist(nextpos, (nx, ny)) + max(objective(c) for c in candidates)
            else:
                # Filter deterministically by distance from nextpos
                candidates2 = sorted(candidates, key=lambda c: dist(nextpos, c))[:12]
                val = 0.6 * (-dist(nextpos, (nx, ny))) + max(objective(c) for c in candidates2)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]