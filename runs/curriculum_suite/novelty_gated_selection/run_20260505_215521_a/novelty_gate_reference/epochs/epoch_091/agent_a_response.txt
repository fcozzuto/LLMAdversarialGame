def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Deterministic tie-breaking order: deltas as listed.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Evaluate by targeting the resource where our "advantage" over opponent is highest.
        # Advantage favors being closer than opponent; also penalizes moves that help opponent.
        best_local = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            # If opponent is already closer, prefer not to chase it strongly.
            # Add slight preference for moving toward any resource quickly.
            val = (do - ds) * 10 - ds

            # Encourage edge-to-edge progression by rewarding resources further "along" the map away from start.
            # (Start corner bias: whichever corner we're closer to than opponent to progress.)
            if sx <= 1 and sy <= 1:
                # moving "toward" upper-right? Actually our start is likely (0,0); prefer larger x or y
                val += (rx + ry) * 0.2
            elif sx >= w - 2 and sy >= h - 2:
                val += ((w - 1 - rx) + (h - 1 - ry)) * 0.2

            # Discourage positions that move adjacent to opponent (risk interception)
            if man(nx, ny, ox, oy) <= 1:
                val -= 3

            if val > best_local:
                best_local = val

        # If we can land on a resource, dominate deterministically.
        if (nx, ny) in resources:
            best_local += 1000

        if best_local > best_val:
            best_val = best_local
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]