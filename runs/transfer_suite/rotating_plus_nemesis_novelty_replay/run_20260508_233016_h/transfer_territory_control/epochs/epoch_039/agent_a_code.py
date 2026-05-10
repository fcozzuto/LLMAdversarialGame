def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer blocking opponent edge-claims by taking frontier cells adjacent to opponent territory.
    neigh4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    frontier = []
    if opp_terr and unclaimed:
        for ux, uy in unclaimed:
            for dx, dy in neigh4:
                ax, ay = ux + dx, uy + dy
                if (ax, ay) in opp_terr:
                    frontier.append((ux, uy))
                    break

    candidates = frontier or list(unclaimed)
    cx, cy = w // 2, h // 2

    if candidates:
        tx, ty = min(candidates, key=lambda c: man(sx, sy, c[0], c[1]) - (3 if c in frontier else 0))
    else:
        tx, ty = (cx, cy)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)

        # Immediate capture value + deterministic progress toward target.
        score = 0.0
        if cell in opp_terr:
            score += 6.0
        elif cell in unclaimed:
            score += 3.0
        elif cell in self_terr:
            score += 1.0
        else:
            score += 0.4

        # Prefer moves that approach the frontier target; slight preference to keep away from obstacles/edges.
        d = max(abs(nx - tx), abs(ny - ty))
        score += -0.8 * d

        ox, oy = opp_pos
        score += 0.08 * (-(abs(nx - ox) + abs(ny - oy)))  # mild pull toward opponent area

        # Discourage corner/edge hugging to counter edge-claim style.
        edge_pen = (nx in (0, w - 1)) + (ny in (0, h - 1))
        score += -0.15 * edge_pen

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]