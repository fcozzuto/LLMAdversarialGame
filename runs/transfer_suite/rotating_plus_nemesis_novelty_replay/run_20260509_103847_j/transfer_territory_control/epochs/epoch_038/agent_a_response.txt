def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Build a deterministic target preference: immediate counterclaim beats expansion when close.
    candidates = []
    for (x, y) in opT:
        d = abs(x - sx) + abs(y - sy)
        if d <= 3:
            candidates.append(((d, x, y), ("op", x, y)))
    if candidates:
        candidates.sort(key=lambda t: t[0])
        tx, ty = candidates[0][1], candidates[0][2]
    else:
        # Expand to nearest unclaimed, with a bias toward edges/corners.
        un_list = list(unT)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        un_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), -((p[0]-cx)**2 + (p[1]-cy)**2), p[0], p[1]))
        if un_list:
            tx, ty = un_list[0]
        else:
            # If nothing else, hold position.
            return [0, 0]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Choose among legal moves by a simple deterministic value function.
    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = 0
        if (nx, ny) in opT:
            val += 6
        elif (nx, ny) in unT:
            val += 3
        elif (nx, ny) in selfT:
            val += 1

        # Move toward the target.
        dist = abs(nx - tx) + abs(ny - ty)
        val += 10 - dist

        # Frontier bias: prefer stepping adjacent to unclaimed (or away from pure interior if chasing is possible).
        if unT:
            adj_un = any((nx + ax, ny + ay) in unT for ax in (-1, 0, 1) for ay in (-1, 0, 1) if not (ax == 0 and ay == 0))
            if adj_un:
                val += 2

        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move