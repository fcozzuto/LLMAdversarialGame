def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))
    if not resources:
        return [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    deltas.sort()  # deterministic tie-break
    best = None
    bestv = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate by best resource to pursue from this move.
        v = -1  # slight preference to move (overstay) if equal later
        if dx == 0 and dy == 0:
            v -= 0.05
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources closer than opponent; also reduce distance to any resource.
            # If opponent is closer, still allow but with strong penalty.
            if do == 0:
                continue
            advantage = (do - ds)  # >0 means we are closer
            v += advantage * 2.0 - ds * 0.6 - 0.05 * cheb(nx, ny, sx, sy)
        # Normalize by number of resources for stability
        v /= float(len(resources))
        # Small preference to reduce distance to current nearest resource
        near_now = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
        near_next = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        v += (near_now - near_next) * 0.8
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best