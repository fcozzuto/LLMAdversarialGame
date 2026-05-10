def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    targets = resources if resources else unclaimed
    if targets:
        # Farthest from opponent to deny sweeping; tie-break by closeness to us.
        tx, ty = max(targets, key=lambda t: (man(ox, oy, t[0], t[1]), -man(sx, sy, t[0], t[1]), -t[0], -t[1]))
    else:
        tx, ty = ox, oy  # fallback

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            # Discourage stepping into obstacles; engine would keep us in place anyway.
            continue

        d_opp = man(ox, oy, nx, ny)
        d_tar = man(nx, ny, tx, ty)

        in_unclaimed = (nx, ny) in set(unclaimed) if unclaimed else False
        in_opp = (nx, ny) in opp_terr

        score = 0
        # Prefer safety/denial and advancing toward our chosen frontier.
        score += 2.0 * d_opp
        score += -1.2 * d_tar
        if in_unclaimed:
            score += 3.0
        if in_opp:
            score += -5.0  # avoid giving the sweeper a flip/extension path

        # Small tie-break to keep deterministic motion preference
        score += -0.01 * (dx * dx + dy * dy)
        score += -0.001 * (dx + 2 * dy)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]