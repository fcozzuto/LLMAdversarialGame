def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_ter = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                self_ter.add((int(p[0]), int(p[1])))
            except:
                pass

    opp_ter = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                opp_ter.add((int(p[0]), int(p[1])))
            except:
                pass

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
    if not unclaimed:
        unclaimed = list(self_ter)[:0]  # empty, handled by fallback

    ter_dist = 999999
    best = None
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    cx = sx
    cy = sy

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if unclaimed:
            nearest = 10**9
            for ux, uy in unclaimed:
                d = man(nx, ny, ux, uy)
                if d < nearest:
                    nearest = d
            score = -nearest
        else:
            score = man(nx, ny, ox, oy)  # fallback: move away from opponent

        if (nx, ny) in opp_ter:
            score -= 1000
        if (nx, ny) in self_ter:
            score += 5
        d_opp = man(nx, ny, ox, oy)
        score += min(20, d_opp) * 0.1

        if score > ter_dist:
            ter_dist = score
            best = [dx, dy]
        elif score == ter_dist and best is not None:
            if dx, dy < tuple(best):
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best