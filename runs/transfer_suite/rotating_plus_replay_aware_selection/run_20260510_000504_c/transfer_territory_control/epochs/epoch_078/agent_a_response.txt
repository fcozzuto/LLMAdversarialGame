def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If we have resources, greedily move toward the first deterministically.
    if resources:
        tx, ty = resources[0]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]

    # Choose a primary target for proximity term
    target = None
    bestd = 10**9
    for (x, y) in unclaimed:
        d = abs(x - sx) + abs(y - sy)
        if d < bestd:
            bestd = d
            target = (x, y)
    if target is None:
        # fallback: head toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        target = (cx, cy)

    # Deterministic candidate order (prefer diagonals)
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1),(0,0)]
    best_move = [0, 0]
    best_score = -10**18

    # If moving onto opponent territory, flipping is enabled.
    # Heuristic: prioritize unclaimed/frontier and opponent cells; also reduce distance to target.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0.0
        pos = (nx, ny)

        if pos in opp_terr:
            sc += 14.0
        if pos in unclaimed:
            sc += 9.0
        if pos in self_terr:
            sc += 1.0

        # Frontier pressure: if next cell is adjacent to our territory (encourage expansion), bonus
        if self_terr:
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in self_terr:
                        sc += 1.8
                        break
                else:
                    continue
                break

        # Proximity to target (target may be floats when using center fallback)
        tx, ty = target
        sc += -0.45 * (abs(nx - tx) + abs(ny - ty))

        # Slightly avoid stepping into "dead corners" if unclaimed is available
        if unclaimed and (nx in (0, w - 1) or ny in (0, h - 1)):
            sc -= 0.6

        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    return best_move