def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    # Target: cells adjacent to opponent territory (prefer unclaimed), to break/flip their center-claim expansion
    frontier = []
    for (ox, oy) in opp_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ox + dx, oy + dy
                if not inb(nx, ny) or (nx, ny) in obst:
                    continue
                if (nx, ny) in self_terr:
                    continue
                if (nx, ny) in unclaimed:
                    frontier.append((nx, ny, 0))
                else:
                    # still allow stepping into opponent-owned to force flip on contact if frontier unclaimed is empty
                    frontier.append((nx, ny, 1))
    targets = [(x, y) for (x, y, pr) in frontier if pr == 0]
    if not targets:
        targets = [(x, y) for (x, y, pr) in frontier if pr == 1]
    if not targets:
        # Fallback: go to nearest unclaimed/resource, else toward opponent position
        for key in ("resources", "unclaimed_cells"):
            v = observation.get(key)
            if isinstance(v, list) and v:
                for p in v:
                    if isinstance(p, (list, tuple)) and len(p) >= 2:
                        targets = [(int(p[0]), int(p[1]))]
                        break
                if targets:
                    break
        if not targets:
            op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
            targets = [(int(op[0]), int(op[1]))]

    # Choose target closest in Manhattan (deterministic)
    tx, ty = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))

    # Greedy one-step toward target with obstacle avoidance; tie-break deterministically
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # Prefer moves that reduce distance to target; slightly prefer unknown territory
        dist = abs(nx - tx) + abs(ny - ty)
        territory_bonus = 0
        if (nx, ny) in unclaimed:
            territory_bonus -= 0.2
        if (nx, ny) in opp_terr:
            territory_bonus -= 0.05  # encourage stepping into opponent-owned if needed (flipping enabled)
        score = (dist + territory_bonus, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]